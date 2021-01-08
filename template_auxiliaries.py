#!/usr/bin/env python3
import time
import nibabel
import numpy as np
from subprocess import check_output
global base, pi, vi, rx, ry, rzes


def warp(fi, ei, typ='r'):
        
    affine = base+fi+'_0GenericAffine.mat'
    nonlin = base+fi+'_1Warp.nii.gz'
    in_tform = ' '.join([nonlin if 's' in typ else '', affine])
    
    mov_data = '_'.join([base+fi,ei,'original.nii.gz'])
    out_data = '_'.join([base+fi,ei,'template.nii.gz'])
    fix_data = '_'.join([base+'average','intensity','template.nii.gz'])            
            
    antsTransformation_call = ' '.join([
        '/groups/ahrens/home/ahrens_lab/ants/bin/antsApplyTransforms',
        '--dimensionality 3',
        '--input', mov_data,
        '--reference-image', fix_data,
        '--output', out_data,
        '--interpolation', pi[ei],
        '--transform', in_tform,
        '--default-value', vi[ei],
        '--verbose 1'
    ])
    
    return(antsTransformation_call.split())


def save_nii(data, fi, ei, ai, dtype='float32'):
        
    rz = rzes[fi]
    nii = nibabel.Nifti1Image(data.astype(dtype), np.diag([rx, ry, rz, 1]))
    nii.header['qform_code'] = 2      # make codes consistent with ANTS
    nii.header['sform_code'] = 1      # 1 scanner, 2 aligned, 3 tlrc, 4 mni.
    nibabel.save(nii, '_'.join([base+fi,ei,ai+'.nii.gz']))


def deploy(cmds, ncor='1'):
    
    def wait_loop(jobs_a, jobs_b):
        for a in jobs_a:
            for b in jobs_b:
                if a==b:
                    return a
        else:
            return 0
    
    jobs_a = []
    for ci in cmds:
        rcmd = ['bsub', '-o', os.path.join(base,'out','%f'%(time.time())), '-n', ncor] + ci
        jobs_a.append(check_output(rcmd).decode().split('>')[0].split('<')[1])
        print('Deployed job %s.'%(jobs_a[-1]))
        
    h = 0
    x = ''
    while 1:
        jobs_b = [j.split(' ')[0] for j in check_output('bjobs').decode().split('\n')]
        
        a = wait_loop(jobs_a, jobs_b)
        if a:
            h = (h+1)%10
            print('%s'%('.' if not h else ''), end='')
            if x!=a:
                x = a;
                print('\nJob %s is still running.'%(x), end='')
            time.sleep(30)
        else:
            print('\nAll jobs completed.\n')
            break

